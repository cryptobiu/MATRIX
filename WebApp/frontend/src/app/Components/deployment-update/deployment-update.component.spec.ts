import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { DeploymentUpdateComponent } from './deployment-update.component';

describe('DeploymentUpdateComponent', () => {
  let component: DeploymentUpdateComponent;
  let fixture: ComponentFixture<DeploymentUpdateComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ DeploymentUpdateComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(DeploymentUpdateComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
