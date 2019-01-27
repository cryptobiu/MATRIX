import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { CompetitionsDetailsComponent } from './competitions-details.component';

describe('CompetitionsDetailsComponent', () => {
  let component: CompetitionsDetailsComponent;
  let fixture: ComponentFixture<CompetitionsDetailsComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ CompetitionsDetailsComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(CompetitionsDetailsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
