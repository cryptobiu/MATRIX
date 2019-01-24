import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { DeploymentResultComponent } from './deployment-result.component';

describe('DeploymentResultComponent', () => {
  let component: DeploymentResultComponent;
  let fixture: ComponentFixture<DeploymentResultComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ DeploymentResultComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(DeploymentResultComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
