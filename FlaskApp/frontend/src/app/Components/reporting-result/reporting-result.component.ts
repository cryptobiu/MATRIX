import { Component, OnInit } from '@angular/core';
import {ActivatedRoute} from "@angular/router";
import {timer} from 'rxjs';
import {IReportingData} from "../../interfaces";
import {DbService} from "../../Services/db.service";
import {ElasticsearchService} from "../../Services/elasticsearch.service";

@Component({
  selector: 'app-reporting-result',
  templateUrl: './reporting-result.component.html',
  styleUrls: ['./reporting-result.component.css']
})
export class ReportingResultComponent implements OnInit {

  public protocolName: string;
  public operation: string;
  public reportingData: Array<IReportingData>;

  constructor(private ac_router: ActivatedRoute, private dbService: DbService, private es: ElasticsearchService) {
    this.protocolName = this.protocolName = this.ac_router.snapshot.paramMap.get('protocolName');
    this.operation = this.ac_router.snapshot.paramMap.get('action');
    this.reportingData = [];

    this.dbService.executeReportingOperation(this.protocolName, this.operation).subscribe(
      value => console.log(value),
      error => console.log(error));
  }

  ngOnInit() {
    this.readData();
  }

  readData(){
    let timerObservable = timer(1000, 10000);
    timerObservable.subscribe(value => this.es.getDocuments('reporting_matrix_ui',
      'execution_matrix_ui', this.protocolName).then(
      response => {
        this.reportingData.length = 0; // clear the data before assign new data
        for (let hit of response.hits.hits)
        {
          let data :IReportingData =
            {
            protocolName: hit._source.protocolName,
            message: hit._source.message,
            timestamp: new Date(hit._source.timestamp)
            };
          this.reportingData.push(data);
        }
      }, error => {
        console.error(error); //error of es
      }),
      err => console.log(err)); //error of timer
  }

}
