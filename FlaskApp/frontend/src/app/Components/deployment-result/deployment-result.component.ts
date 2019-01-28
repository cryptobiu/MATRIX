import {Component, Injectable, OnInit} from '@angular/core';
import {ActivatedRoute} from "@angular/router";
import {DbService} from "../../Services/db.service";
import {timer} from 'rxjs';
import {ElasticsearchService} from "../../Services/elasticsearch.service";
import {IDeploymentData} from "../../interfaces";

@Component({
  selector: 'app-deployment-result',
  templateUrl: './deployment-result.component.html',
  styleUrls: ['./deployment-result.component.css']
})

@Injectable()
export class DeploymentResultComponent implements OnInit {

  public protocolName: string;
  private operation: string;
  public deploymentData: Array<IDeploymentData>;


  constructor(private ac_router: ActivatedRoute, private dbService: DbService, private es: ElasticsearchService) {
    this.protocolName = this.ac_router.snapshot.paramMap.get('protocolName');
    this.operation = this.ac_router.snapshot.paramMap.get('action');
    this.deploymentData = [];
    this.dbService.executeDeployOperation(this.protocolName, this.operation).subscribe(
      value => console.log(value),
      error => console.log(error));
  }

  ngOnInit() {
    this.readData();
  }

   readData(){

    let timerObservable = timer(1000, 10000);
    timerObservable.subscribe(value => this.es.getDocuments('deployment_matrix_ui',
      'deployment_matrix_ui').then(
      response => {
        for (let hit of response.hits.hits)
        {
          let data :IDeploymentData =
            {
            protocolName: hit._source.protocolName,
            message: hit._source.message,
            timestamp: new Date(hit._source.timestamp)
            };
          this.deploymentData.push(data);
        }
      }, error => {
        console.error(error); //error of es
      }),
      err => console.log(err)); //error of timer
  }
}
