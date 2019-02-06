import {ICompetition} from "./interfaces";

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

export class Competition implements ICompetition{
  constructor(public name: string, public description: string, public startDate: Date,
              public endDate: Date, public participants: [])
  {}
}

