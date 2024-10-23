// Don't check if oldPod has the finalizer, as during ownership transfer
// finalizers might be re-added and removed again in behalf of the new owner.
// If all those Pod updates collapse into a single event, the finalizer
// might be removed in oldPod and curPod. We want to record the latest
// state.
finalizerRemoved := !hasJobTrackingFinalizer(curPod)
curControllerRef := metav1.GetControllerOf(curPod)
oldControllerRef := metav1.GetControllerOf(oldPod)
controllerRefChanged := !reflect.DeepEqual(curControllerRef, oldControllerRef)
if controllerRefChanged && oldControllerRef != nil {
	// The ControllerRef was changed. Sync the old controller, if any.
	if job := jm.resolveControllerRef(oldPod.Namespace, oldControllerRef); job != nil {
		if finalizerRemoved {
			key, err := controller.KeyFunc(job)
			if err == nil {
				jm.finalizerExpectations.finalizerRemovalObserved(key, string(curPod.UID))
			}
		}
		jm.enqueueControllerPodUpdate(job, immediate)
	}
}
