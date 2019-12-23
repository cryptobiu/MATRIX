import { Component, OnInit } from '@angular/core';
import { Observable } from 'rxjs/';
import { DataSource } from '@angular/cdk/collections';
import { DbService } from '../../Services/db.service';
import { AuthService } from '../../Services/auth.service';
import { Router } from '@angular/router';
import {Protocol} from '../../classes';
import {DownloadFileService} from '../../Services/download-file.service';


@Component({
  selector: 'app-protocol-deployment',
  templateUrl: './deployment.component.html',
  styleUrls: ['./deployment.component.css']
})
export class DeploymentComponent implements OnInit {
  dataSource = new ProtocolDataSource(this.dbService);
  displayedColumns = ['name', 'action', 'update', 'downloadLog', 'downloadConf'];
  actions = ['Deploy Instance(s)', 'Create key pair(s)', 'Create security group',
    'Update network details', 'Terminate machines', 'Change machines types', 'Start instances', 'Stop instances'];

  constructor(private dbService: DbService, private auth: AuthService, private router: Router,
              private fileDownloadService: DownloadFileService) {
    if (!localStorage.getItem('isLoggedIn')) {
      this.router.navigate(['/login']).catch(function (err) {
        if (err) {
          console.error(err);
        }
      });
    }
  }

  ngOnInit() {
  }

  onChange(operation, protocol) {
    this.router.navigate(['/deployment/' + protocol + '/' + operation]).catch(function (err) {
      if (err) {
        console.error(err);
      }
    });
  }

  getLogFile(protocolName: string) {
    this.fileDownloadService.getDeploymentLogs(protocolName).subscribe(
      response => {
        const file = new Blob([response]);
        const data = window.URL.createObjectURL(file);
        const downloadLink = document.createElement('a');
        downloadLink.href = data;
        downloadLink.download = protocolName + '_deployment.log';

        // this is necessary as link.click() does not work on the latest firefox
        downloadLink.dispatchEvent(new MouseEvent('click',
          { bubbles: true, cancelable: true, view: window }));
        setTimeout(function () {
          // For Firefox it is necessary to delay revoking the ObjectURL
          window.URL.revokeObjectURL(data);
          downloadLink.remove();
        });
      },
      error => alert('Problem during download')
    );
  }

  getConfFile(protocolName: string) {
    this.fileDownloadService.getDeploymentConf(protocolName).subscribe(
      response => {
        const file = new Blob([response]);
        const data = window.URL.createObjectURL(file);
        const downloadLink = document.createElement('a');
        downloadLink.href = data;
        downloadLink.download = protocolName + '_deployment_conf.json';

        // this is necessary as link.click() does not work on the latest firefox
        downloadLink.dispatchEvent(new MouseEvent('click',
          { bubbles: true, cancelable: true, view: window }));
        setTimeout(function () {
          // For Firefox it is necessary to delay revoking the ObjectURL
          window.URL.revokeObjectURL(data);
          downloadLink.remove();
        });
      },
      error => alert('Problem during download')
    );
  }
}


export class ProtocolDataSource extends DataSource<any> {
  constructor(private dbService: DbService) {
    super();
  }

  connect(): Observable<Protocol[]> {
    return this.dbService.getProtocols();
  }

  disconnect() {}
}
