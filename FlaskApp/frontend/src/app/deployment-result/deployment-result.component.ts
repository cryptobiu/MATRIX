import {Component, Injectable, OnInit} from '@angular/core';
import {ActivatedRoute} from "@angular/router";
import {DbService} from "../db.service";
import {timer} from 'rxjs';
import {MessagesService} from "../messages.service";
import {IMessage} from "../interfaces";
import {ElasticsearchService} from "../elasticsearch.service";

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


  constructor(private ac_router: ActivatedRoute, private dbService: DbService,
              private messages: MessagesService) { }

  ngOnInit() {
    this.protocolName = this.ac_router.snapshot.paramMap.get('protocolName');
    this.operation = this.ac_router.snapshot.paramMap.get('action');
    this.dbService.executeDeployOperation(this.protocolName, this.operation).subscribe();
    this.messages.messages.subscribe(msg => {
      this.fileData.push(msg);
    })
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






