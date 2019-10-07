export interface ICompetition
{
  name: string;
  startDate: Date;
  endDate: Date;
  description: string;
  participants: [];
}

export interface IProtocol {
  protocolName: string;
  repoAddress: string;
  securityLevel: string;
  thresholdLevel: string;
}

export interface IReportingData {
  protocolName: string;
  message: string;
  timestamp: Date;
}
