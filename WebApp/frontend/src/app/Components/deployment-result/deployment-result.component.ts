import {Component, Injectable, OnInit} from '@angular/core';
import {ActivatedRoute} from "@angular/router";
import {DbService} from "../../Services/db.service";
import {timer} from 'rxjs';

@Component({
  selector: 'app-deployment-result',
  templateUrl: './deployment-result.component.html',
  styleUrls: ['./deployment-result.component.css']
})

@Injectable()
export class DeploymentResultComponent implements OnInit {

  public protocolName: string;
  private operation: string;
  public deploymentData: string[];


  constructor(private ac_router: ActivatedRoute, private dbService: DbService) {
    this.protocolName = this.ac_router.snapshot.paramMap.get('protocolName');
    this.operation = this.ac_router.snapshot.paramMap.get('action');
    this.deploymentData = [];
    this.dbService.executeDeployOperation(this.protocolName, this.operation).subscribe(
      value => console.log(value),
      error => console.log(error));
  }

  ngOnInit() {
    this.readData();
  }

   readData(){
    let timeObservable = timer(1000,10000);
    timeObservable.subscribe(value => this.dbService.getDeploymentData(this.protocolName).subscribe(
      response => {
        this.deploymentData = response.toString().split(',');
      },
      error => console.log(error)
      ),
      err => console.log(err));
  }
}
