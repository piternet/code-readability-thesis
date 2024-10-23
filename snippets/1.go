for i, metricSpec := range metricSpecs {
	replicaCountProposal, metricNameProposal, timestampProposal, condition, err := a.computeReplicasForMetric(ctx, hpa, metricSpec, specReplicas, statusReplicas, selector, statuses[i])

	if err != nil {
		if invalidMetricsCount <= 0 {
			invalidMetricCondition = condition
			invalidMetricError = err
		}
		invalidMetricsCount++
	}
	if err == nil && (replicas == 0 || replicaCountProposal > replicas) {
		timestamp = timestampProposal
		replicas = replicaCountProposal
		metric = metricNameProposal
	}
}
