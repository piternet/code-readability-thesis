cm := controller.NewPodControllerRefManager(jm.podControl, j, selector, controllerKind, canAdoptFunc, finalizers...)
// When adopting Pods, this operation adds an ownerRef and finalizers.
pods, err = cm.ClaimPods(ctx, pods)
if err != nil || !withFinalizers {
	return pods, err
}
// Set finalizer on adopted pods for the remaining calculations.
for i, p := range pods {
	adopted := true
	for _, r := range p.OwnerReferences {
		if r.UID == j.UID {
			adopted = false
			break
		}
	}
	if adopted && !hasJobTrackingFinalizer(p) {
		pods[i] = p.DeepCopy()
		pods[i].Finalizers = append(p.Finalizers, batch.JobTrackingFinalizer)
	}
}
