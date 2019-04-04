import { Component, OnInit } from '@angular/core';
import { Observable } from 'rxjs/';
import { DataSource } from '@angular/cdk/collections';
import { DbService } from "../../Services/db.service";
import { AuthService } from "../../Services/auth.service";
import { IProtocol } from "../../interfaces";
import { Router } from "@angular/router";


@Component({
  selector: 'app-protocol-deployment',
  templateUrl: './deployment.component.html',
  styleUrls: ['./deployment.component.css']
})
export class DeploymentComponent implements OnInit {
  dataSource = new ProtocolDataSource(this.dbService);
  displayedColumns = ['name', 'action'];
  actions = ['Deploy Instance(s)', 'Create key pair(s)', 'Create security group', 'Update network details', 'Terminate machines',
    'Change machines types', 'Start instances', 'Stop instances'];

  constructor(private dbService:DbService, private auth: AuthService, private router : Router)
  {
    // if (!this.auth.isAuthenticated())
    //   this.router.navigate([this.auth.login()]);
  }

  ngOnInit() {
  }

  onChange(operation, protocol){
    this.router.navigate(['/deployment/' + protocol + '/' + operation])
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
