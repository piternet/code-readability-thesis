for i := range sharedClusterRole.AggregationRule.ClusterRoleSelectors {
	selector := sharedClusterRole.AggregationRule.ClusterRoleSelectors[i]
	runtimeLabelSelector, err := metav1.LabelSelectorAsSelector(&selector)
	if err != nil {
		return err
	}
	clusterRoles, err := c.clusterRoleLister.List(runtimeLabelSelector)
	if err != nil {
		return err
	}
	sort.Sort(byName(clusterRoles))

	for i := range clusterRoles {
		if clusterRoles[i].Name == sharedClusterRole.Name {
			continue
		}

		for j := range clusterRoles[i].Rules {
			currRule := clusterRoles[i].Rules[j]
			if !ruleExists(newPolicyRules, currRule) {
				newPolicyRules = append(newPolicyRules, currRule)
			}
		}
	}
}
