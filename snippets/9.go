if diff < 0 {
	diff *= -1
	if diff > rsc.burstReplicas {
		diff = rsc.burstReplicas
	}
	// TODO: Track UIDs of creates just like deletes. The problem currently
	// is we'd need to wait on the result of a create to record the pod's
	// UID, which would require locking *across* the create, which will turn
	// into a performance bottleneck. We should generate a UID for the pod
	// beforehand and store it via ExpectCreations.
	rsc.expectations.ExpectCreations(rsKey, diff)
	klog.V(2).InfoS("Too few replicas", "replicaSet", klog.KObj(rs), "need", *(rs.Spec.Replicas), "creating", diff)
	// Batch the pod creates. Batch sizes start at SlowStartInitialBatchSize
	// and double with each successful iteration in a kind of "slow start".
	// This handles attempts to start large numbers of pods that would
	// likely all fail with the same error. For example a project with a
	// low quota that attempts to create a large number of pods will be
	// prevented from spamming the API service with the pod create requests
	// after one of its pods fails.  Conveniently, this also prevents the
	// event spam that those failures would generate.
	successfulCreations, err := slowStartBatch(diff, controller.SlowStartInitialBatchSize, func() error {
		err := rsc.podControl.CreatePods(ctx, rs.Namespace, &rs.Spec.Template, rs, metav1.NewControllerRef(rs, rsc.GroupVersionKind))
		if err != nil {
			if apierrors.HasStatusCause(err, v1.NamespaceTerminatingCause) {
				// if the namespace is being terminated, we don't have to do
				// anything because any creation will fail
				return nil
			}
		}
		return err
	})

	// Any skipped pods that we never attempted to start shouldn't be expected.
	// The skipped pods will be retried later. The next controller resync will
	// retry the slow start process.
	if skippedPods := diff - successfulCreations; skippedPods > 0 {
		klog.V(2).Infof("Slow-start failure. Skipping creation of %d pods, decrementing expectations for %v %v/%v", skippedPods, rsc.Kind, rs.Namespace, rs.Name)
		for i := 0; i < skippedPods; i++ {
			// Decrement the expected number of creates because the informer won't observe this pod
			rsc.expectations.CreationObserved(rsKey)
		}
	}
	return err
}
