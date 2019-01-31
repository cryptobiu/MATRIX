export class Protocol {
  constructor(
    public protocolName: string,
    public repoAddress: string,
    public securityLevel: string,
    public thresholdLevel: string,
  ){}
}
export class CompetitionRegistration {
  constructor(
    public protocolName: string,
    public institute: string,
  ){}
}

