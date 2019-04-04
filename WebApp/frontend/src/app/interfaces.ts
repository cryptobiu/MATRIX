export interface ICompetition
{
  name: string,
  startDate: Date,
  endDate: Date,
  description: string;
  participants: [];
}

export interface IProtocol {
  name: string,
  repoAddress: string,
  securityLevel: string,
  securityThreshold: string
}

export interface IReportingData {
  protocolName: string;
  message: string;
  timestamp: Date;
}
