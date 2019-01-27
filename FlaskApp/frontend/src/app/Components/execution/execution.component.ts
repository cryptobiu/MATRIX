import { Component, OnInit } from '@angular/core';
import { Observable } from 'rxjs/';
import {DataSource} from '@angular/cdk/collections';
import {DbService} from "../../Services/db.service";
import {IProtocol} from "../../interfaces";

@Component({
  selector: 'app-execution',
  templateUrl: './execution.component.html',
  styleUrls: ['./execution.component.css']
})
export class ExecutionComponent implements OnInit {

  dataSource = new ProtocolDataSource(this.dbService);
  displayedColumns = ['name', 'action'];
  actions = ['Install Experiment', 'Execute Experiment', 'Execute Experiment with profiler', 'Update libscapi'];

  constructor(private dbService:DbService) { }

  ngOnInit() {
  }

  onChange(value, protocol){
    //TODO: Implement the requested execution action.
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
