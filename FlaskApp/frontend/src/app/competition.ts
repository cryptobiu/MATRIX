export class Competition {
  _id: string;
  name: string;
  startData: Date;
  endtData: Date;
}

export interface ICompetition
{
  name: string,
  startData: Date,
  endData: Date,
  description: string;

}
