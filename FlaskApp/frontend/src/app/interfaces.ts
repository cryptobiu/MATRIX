export interface ICompetition
{
  name: string,
  startData: Date,
  endData: Date,
  description: string;
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
