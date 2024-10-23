// doSetConfigCmd a wrapper function to be used by SetConfig
func (i *Handle) doSetConfigCmd(c *Config) error {
	req := newIPVSRequest(ipvsCmdSetConfig)
	req.Seq = atomic.AddUint32(&i.seq, 1)

	req.AddData(nl.NewRtAttr(ipvsCmdAttrTimeoutTCP, nl.Uint32Attr(uint32(c.TimeoutTCP.Seconds()))))
	req.AddData(nl.NewRtAttr(ipvsCmdAttrTimeoutTCPFin, nl.Uint32Attr(uint32(c.TimeoutTCPFin.Seconds()))))
	req.AddData(nl.NewRtAttr(ipvsCmdAttrTimeoutUDP, nl.Uint32Attr(uint32(c.TimeoutUDP.Seconds()))))

	_, err := execute(i.sock, req, 0)

	return err
}
