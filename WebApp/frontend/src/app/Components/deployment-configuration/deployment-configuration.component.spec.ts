import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { DeploymentConfigurationComponent } from './deployment-configuration.component';

describe('DeploymentConfigurationComponent', () => {
  let component: DeploymentConfigurationComponent;
  let fixture: ComponentFixture<DeploymentConfigurationComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ DeploymentConfigurationComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(DeploymentConfigurationComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
