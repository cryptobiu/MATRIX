import {Component, OnInit} from '@angular/core';
import {DbService} from '../../Services/db.service';
import {ActivatedRoute, Router} from '@angular/router';
import {Protocol} from '../../classes';

@Component({
  selector: 'app-execution-configuration',
  templateUrl: './execution-configuration.component.html',
  styleUrls: ['./execution-configuration.component.css']
})
export class ExecutionConfigurationComponent implements OnInit {

  public protocolModel: Protocol;
  public numberOfConfigurations: number;
  public configurations: Array<string>;
  public numberOfIterations: number;
  public workingDirectory: string;
  public resultsDirectory: string;

  constructor(private dbService: DbService, private router: Router, private acRouter: ActivatedRoute) {
    const protocolName = this.acRouter.snapshot.paramMap.get('protocolName');

    this.dbService.getProtocol(protocolName).
    subscribe(val => {
      this.protocolModel = new Protocol(val);
      this.numberOfConfigurations = this.protocolModel.numConfigurations;
      this.configurations = new Array<string>();
      for (const conf of this.protocolModel.configurations) {
        this.configurations.push(conf.split('@').join( ' '));
      }
      this.numberOfIterations = this.protocolModel.numOfIterations;
      this.workingDirectory = this.protocolModel.workingDirectory;
      this.resultsDirectory = this.protocolModel.resultsDirectory;
    }, error => console.error(error));
  }

  ngOnInit() {
    this.protocolModel = new Protocol();
  }

}
