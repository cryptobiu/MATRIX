import { Component, OnInit } from '@angular/core';
import {ActivatedRoute} from '@angular/router';
import {timer} from 'rxjs';
import {DbService} from '../../Services/db.service';

@Component({
  selector: 'app-execution-result',
  templateUrl: './execution-result.component.html',
  styleUrls: ['./execution-result.component.css']
})
export class ExecutionResultComponent implements OnInit {

  public protocolName: string;
  public operation: string;
  public executionData: string[];

  constructor(private ac_router: ActivatedRoute, private dbService: DbService) {
    this.protocolName = this.protocolName = this.ac_router.snapshot.paramMap.get('protocolName');
    this.operation = this.ac_router.snapshot.paramMap.get('action');
    this.executionData = [];
    this.dbService.executeExecutionOperation(this.protocolName, this.operation).subscribe(
      value => console.log(value),
      error => console.log(error));
  }

  ngOnInit() {
    this.readData();
  }

  readData() {
    const timeObservable = timer(5000, 5000);
    timeObservable.subscribe(value => this.dbService.getExecutionData(this.protocolName).subscribe(
      response => {
        this.executionData = response.toString().split(',');
      },
      error => console.log(error)
      ),
      err => console.log(err));
  }
}
