export interface ICompetition
{
  name: string;
  startDate: Date;
  endDate: Date;
  description: string;
  participants: [];
}

export interface IReportingData {
  protocolName: string;
  message: string;
  timestamp: Date;
}
