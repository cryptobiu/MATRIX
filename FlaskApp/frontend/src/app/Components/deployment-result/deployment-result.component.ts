import {Component, Injectable, OnInit} from '@angular/core';
import {ActivatedRoute} from "@angular/router";
import {DbService} from "../../Services/db.service";
import {timer} from 'rxjs';
import {ElasticsearchService} from "../../Services/elasticsearch.service";

@Component({
  selector: 'app-deployment-result',
  templateUrl: './deployment-result.component.html',
  styleUrls: ['./deployment-result.component.css'],
  providers: [ElasticsearchService]
})

@Injectable()
export class DeploymentResultComponent implements OnInit {

  private protocolName: string;
  private operation: string;
  private fileData: string[];


  constructor(private ac_router: ActivatedRoute, private dbService: DbService) { }

  ngOnInit() {
    this.protocolName = this.ac_router.snapshot.paramMap.get('protocolName');
    this.operation = this.ac_router.snapshot.paramMap.get('action');
    this.dbService.executeDeployOperation(this.protocolName, this.operation).subscribe();
  }

  // sendMsg(){
  //   let message = {
  //     'message': 'test'
  //   };
  //   this.webService.messages.next(message);
  // }
  //
  // readData(){
  //
  //   let timerObservable = timer(1000, 10000);
  //   timerObservable.subscribe(value =>  this.fileData=this.es.getDocuments(),
  //     err => console.log(err));
  // }
}






