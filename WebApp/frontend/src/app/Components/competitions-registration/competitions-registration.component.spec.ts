import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { CompetitionsRegistrationComponent } from './competitions-registration.component';

describe('CompetitionsRegistrationComponent', () => {
  let component: CompetitionsRegistrationComponent;
  let fixture: ComponentFixture<CompetitionsRegistrationComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ CompetitionsRegistrationComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(CompetitionsRegistrationComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
