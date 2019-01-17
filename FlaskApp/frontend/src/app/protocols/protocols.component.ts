import { Component, OnInit } from '@angular/core';
import { Observable } from 'rxjs/';
import {DataSource} from '@angular/cdk/collections';
import {DbService} from "../db.service";
import {IProtocol} from "../interfaces";

@Component({
  selector: 'app-protocols',
  templateUrl: './protocols.component.html',
  styleUrls: ['./protocols.component.css']
})
export class ProtocolsComponent implements OnInit {

  dataSource = new ProtocolDataSource(this.dbService);
  displayedColumns = ['name', 'security', 'threshold'];
  constructor(private dbService: DbService) { }

  ngOnInit() {
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
