func (h *handler) Execute(_ []string, r <-chan svc.ChangeRequest, s chan<- svc.Status) (bool, uint32) {
	s <- svc.Status{State: svc.StartPending, Accepts: 0}
	// Unblock initService()
	h.fromsvc <- nil

	s <- svc.Status{State: svc.Running, Accepts: svc.AcceptStop | svc.AcceptShutdown | svc.Accepted(windows.SERVICE_ACCEPT_PARAMCHANGE)}
	klog.Infof("Service running")
Loop:
	for {
		select {
		case <-h.tosvc:
			break Loop
		case c := <-r:
			switch c.Cmd {
			case svc.Cmd(windows.SERVICE_CONTROL_PARAMCHANGE):
				s <- c.CurrentStatus
			case svc.Interrogate:
				s <- c.CurrentStatus
			case svc.Stop, svc.Shutdown:
				klog.Infof("Service stopping")
				// We need to translate this request into a signal that can be handled by the signal handler
				// handling shutdowns normally (currently apiserver/pkg/server/signal.go).
				// If we do not do this, our main threads won't be notified of the upcoming shutdown.
				// Since Windows services do not use any console, we cannot simply generate a CTRL_BREAK_EVENT
				// but need a dedicated notification mechanism.
				graceful := server.RequestShutdown()

				// Free up the control handler and let us terminate as gracefully as possible.
				// If that takes too long, the service controller will kill the remaining threads.
				// As per https://docs.microsoft.com/en-us/windows/desktop/services/service-control-handler-function
				s <- svc.Status{State: svc.StopPending}

				// If we cannot exit gracefully, we really only can exit our process, so at least the
				// service manager will think that we gracefully exited. At the time of writing this comment this is
				// needed for applications that do not use signals (e.g. kube-proxy)
				if !graceful {
					go func() {
						// Ensure the SCM was notified (The operation above (send to s) was received and communicated to the
						// service control manager - so it doesn't look like the service crashes)
						time.Sleep(1 * time.Second)
						os.Exit(0)
					}()
				}
				break Loop
			}
		}
	}

	return false, 0
}
