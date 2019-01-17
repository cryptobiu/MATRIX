import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { ProtocolDeploymentComponent } from './protocol-deployment.component';

describe('ProtocolDeploymentComponent', () => {
  let component: ProtocolDeploymentComponent;
  let fixture: ComponentFixture<ProtocolDeploymentComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ ProtocolDeploymentComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(ProtocolDeploymentComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
