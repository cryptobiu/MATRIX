import { Component, OnInit } from '@angular/core';
import {DataSource} from "@angular/cdk//collections";
import {DbService} from "../db.service";
import {Observable} from "rxjs";
import {IProtocol} from "../interfaces";

@Component({
  selector: 'app-reporting',
  templateUrl: './reporting.component.html',
  styleUrls: ['./reporting.component.css']
})
export class ReportingComponent implements OnInit {
  dataSource = new ReportingDataSource(this.dbService);
  displayedColumns = ['name', 'action'];
  actions = ['Analyze Results using Excel', 'Analyze Results using Elasticsearch'];
  constructor(private dbService:DbService) { }

  ngOnInit() {
  }

  onChange(value, protocol){
        //TODO: Implement the requested reporting action.
  }

}

export class ReportingDataSource extends DataSource<any> {
  constructor(private dbService:DbService) {
    super()
  }

  connect(): Observable<IProtocol[]> {
    return this.dbService.getProtocols();
  }

  disconnect() {}
}

