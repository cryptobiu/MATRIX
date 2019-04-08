import { Component, OnInit } from '@angular/core';
import { Observable } from 'rxjs/';
import {DataSource} from '@angular/cdk/collections';
import {DbService} from "../../Services/db.service";
import {IProtocol} from "../../interfaces";
import {Router} from "@angular/router";

@Component({
  selector: 'app-execution',
  templateUrl: './execution.component.html',
  styleUrls: ['./execution.component.css']
})
export class ExecutionComponent implements OnInit {

  dataSource = new ProtocolDataSource(this.dbService);
  displayedColumns = ['name', 'action'];
  actions = ['Install Experiment', 'Execute Experiment', 'Execute Experiment with profiler',
    'Get Logs', 'Update libscapi'];

  constructor(private dbService:DbService, private router: Router)
  {
    if (!localStorage.getItem('isLoggedIn'))
      this.router.navigate(['/login']);
  }

  ngOnInit() {
  }

  onChange(operation, protocol){
    this.router.navigate(['/execution/' + protocol + '/' + operation])
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
