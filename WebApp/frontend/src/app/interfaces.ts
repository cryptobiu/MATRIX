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

export interface IProtocolData {
  protocolName: string;
  numberOfParties: number;
  machineType: string;
  regions: string[];
  configurations: string[];
}

export interface IDeploymentData {
  protocolName: string;
  message: string;
  timestamp: Date;
}

export interface IExecutionData {
  protocolName: string;
  message: string;
  timestamp: Date;
}

export interface IReportingData {
  protocolName: string;
  message: string;
  timestamp: Date;
}
