import {ICompetition} from './interfaces';

export class Protocol {
  constructor(
    public protocolName: string,
    public cloudProviders: {},
    public executableName: string,
    public numConfigurations: number,
    public configurations: [],
    public numOfIterations: number,
    public workingDirectory: string,
    public resultsDirectory: string,
    public institute: string,
    public securityLevel: string,
    public thresholdLevel: string,
  ) {}
}
export class CompetitionRegistration {
  constructor(
    public protocolName: string,
    public institute: string,
  ) {}
}

export class Competition implements ICompetition{
  constructor(public name: string, public description: string, public startDate: Date,
              public endDate: Date, public participants: []) {}
}

