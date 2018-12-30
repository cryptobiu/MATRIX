import { Component, OnInit } from '@angular/core';
import {DbService} from "../db.service";

@Component({
  selector: 'app-protocols',
  templateUrl: './protocols.component.html',
  styleUrls: ['./protocols.component.css']
})
export class ProtocolsComponent implements OnInit {

  public protocols = [];
  constructor(private dbService: DbService) { }

  ngOnInit() {
    this.dbService.getProtocols()
      .subscribe(data => this.protocols = data);
  }

}
