import { Component, OnInit } from '@angular/core';
import {ActivatedRoute} from "@angular/router";
import {timer} from 'rxjs';
import {IExecutionData} from "../../interfaces";
import {DbService} from "../../Services/db.service";
import {ElasticsearchService} from "../../Services/elasticsearch.service";

@Component({
  selector: 'app-execution-result',
  templateUrl: './execution-result.component.html',
  styleUrls: ['./execution-result.component.css']
})
export class ExecutionResultComponent implements OnInit {

  private protocolName: string;
  private operation: string;
  private executionData: Array<IExecutionData>;

  constructor(private ac_router: ActivatedRoute, private dbService: DbService, private es: ElasticsearchService) {
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

  readData(){
    let timerObservable = timer(1000, 10000);
    timerObservable.subscribe(value => this.es.getDocuments('execution_matrix_ui',
      'execution_matrix_ui', this.protocolName).then(
      response => {
        for (let hit of response.hits.hits)
        {
          let data :IExecutionData =
            {
            protocolName: hit._source.protocolName,
            message: hit._source.message,
            timestamp: new Date(hit._source.timestamp)
            };
          this.executionData.push(data);
        }
      }, error => {
        console.error(error); //error of es
      }),
      err => console.log(err)); //error of timer
  }
}
