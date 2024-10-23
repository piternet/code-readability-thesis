// isPodStatusByKubeletEqual returns true if the given pod statuses are equal when non-kubelet-owned
// pod conditions are excluded.
// This method normalizes the status before comparing so as to make sure that meaningless
// changes will be ignored.
func isPodStatusByKubeletEqual(oldStatus, status *v1.PodStatus) bool {
	oldCopy := oldStatus.DeepCopy()
	for _, c := range status.Conditions {
		if kubetypes.PodConditionByKubelet(c.Type) {
			_, oc := podutil.GetPodCondition(oldCopy, c.Type)
			if oc == nil || oc.Status != c.Status || oc.Message != c.Message || oc.Reason != c.Reason {
				return false
			}
		}
	}
	oldCopy.Conditions = status.Conditions
	return apiequality.Semantic.DeepEqual(oldCopy, status)
}
