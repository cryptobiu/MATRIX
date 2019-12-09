import {ICompetition} from './interfaces';

export class Protocol {
  public protocolName: string;
  public cloudProviders: {};
  public executableName: string;
  public numConfigurations: number;
  public configurations: [];
  public numOfIterations: number;
  public workingDirectory: string;
  public resultsDirectory: string;
  public institute: string;
  public securityLevel: string;
  public thresholdLevel: string;
  public relatedArticle: string;

  constructor(p: Protocol) {
    this.protocolName = p.protocolName;
    this.cloudProviders = p.cloudProviders;
    this.executableName = p.executableName;
    this.configurations = p.configurations;
    this.numConfigurations = p.numConfigurations;
    this.workingDirectory = p.workingDirectory;
    this.resultsDirectory = p.resultsDirectory;
    this.institute = p.institute;
    this.securityLevel = p.securityLevel;
    this.thresholdLevel = p.thresholdLevel;
    this.relatedArticle = p.relatedArticle;
  }

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

