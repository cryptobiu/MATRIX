import {ICompetition} from './interfaces';

export class Protocol {
  public protocolName: string;
  public cloudProviders: {};
  public executableName: string;
  public numConfigurations: number;
  public configurations: Array<string>;
  public numOfIterations: number;
  public workingDirectory: string;
  public resultsDirectory: string;
  public institute: string;
  public securityLevel: string;
  public thresholdLevel: string;
  public relatedArticle: string;

  constructor(params: Protocol = {} as Protocol) {
    const {
      protocolName = '',
      cloudProviders = {},
      executableName = '',
      configurations = [],
      numConfigurations = 0,
      workingDirectory = '',
      resultsDirectory = '',
      institute = '',
      securityLevel = '',
      thresholdLevel = '',
      relatedArticle = ''
         } = params;
    this.protocolName = protocolName;
    this.cloudProviders = cloudProviders;
    this.executableName = executableName;
    this.configurations =  [...configurations];
    this.numConfigurations = numConfigurations;
    this.workingDirectory = workingDirectory;
    this.resultsDirectory = resultsDirectory;
    this.institute = institute;
    this.securityLevel = securityLevel;
    this.thresholdLevel = thresholdLevel;
    this.relatedArticle = relatedArticle;
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

