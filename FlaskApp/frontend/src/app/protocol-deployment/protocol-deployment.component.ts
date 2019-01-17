import { Component, OnInit } from '@angular/core';
import { Observable } from 'rxjs/';
import {DataSource} from '@angular/cdk/collections';
import {DbService} from "../db.service";
import {IProtocol} from "../interfaces";


@Component({
  selector: 'app-protocol-deployment',
  templateUrl: './protocol-deployment.component.html',
  styleUrls: ['./protocol-deployment.component.css']
})
export class ProtocolDeploymentComponent implements OnInit {
  dataSource = new ProtocolDataSource(this.dbService);
  displayedColumns = ['name', 'action'];
  actions = ['Deploy Instance(s)', 'Create Key pair(s)', 'Update network details', 'Terminate machines',
    'Change machines types', 'Start instances', 'Stop instances'];

  constructor(private dbService:DbService) { }

  ngOnInit() {
  }

  onChange(value, protocol){
    //TODO: Implement the requested deployment action.
  }

}

export class ProtocolDataSource extends DataSource<any> {
  constructor(private dbService:DbService) {
    super();
  }

  connect(): Observable<IProtocol[]> {
    return this.dbService.getProtocols();
  }

  disconnect() {}
}
