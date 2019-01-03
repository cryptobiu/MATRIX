import { Component, OnInit } from '@angular/core';
import {ActivatedRoute, Router} from "@angular/router";
import {DbService} from "../db.service";
import {IProtocolData} from "../interfaces";

@Component({
  selector: 'app-protocols-details',
  templateUrl: './protocols-details.component.html',
  styleUrls: ['./protocols-details.component.css']
})
export class ProtocolsDetailsComponent implements OnInit {

  private protocolName: string;
  private protocolData: IProtocolData;
  private fileData: string;
  constructor(private ac_router: ActivatedRoute, private router:Router, private dbService: DbService) { }

  ngOnInit() {
    let name = this.ac_router.snapshot.paramMap.get('name');
    this.protocolName = name;
    this.dbService.getProtocolDate(name).
    subscribe(data => this.protocolData = data);
  }

  onSubmit(){
    this.dbService.executeProtocol(this.protocolName).
    subscribe(data => this.router.navigate(['/protocols/execution/' + this.protocolName]));
  }

}
