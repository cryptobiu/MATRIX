import { Component, OnInit } from '@angular/core';
import {ActivatedRoute} from '@angular/router';
import {timer} from 'rxjs';
import {DbService} from '../../Services/db.service';

@Component({
  selector: 'app-reporting-result',
  templateUrl: './reporting-result.component.html',
  styleUrls: ['./reporting-result.component.css']
})
export class ReportingResultComponent implements OnInit {

  public protocolName: string;
  public operation: string;
  public reportingData: string[];

  constructor(private ac_router: ActivatedRoute, private dbService: DbService) {
    this.protocolName = this.ac_router.snapshot.paramMap.get('protocolName');
    this.operation = this.ac_router.snapshot.paramMap.get('action');
    this.reportingData = [];

    this.dbService.executeReportingOperation(this.protocolName, this.operation).subscribe(
      value => console.log(value),
      error => console.log(error));
  }

  ngOnInit() {
    this.readData();
  }

  readData() {
    const timeObservable = timer(1000, 10000);
    timeObservable.subscribe(value => this.dbService.getReportingData(this.protocolName).subscribe(
      response => {
        this.reportingData = response.toString().split(',');
      },
      error => console.log(error)
      ),
      err => console.log(err));
  }
}
