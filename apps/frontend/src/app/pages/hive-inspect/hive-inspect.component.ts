import { ChangeDetectionStrategy, Component, inject, signal } from '@angular/core';
import { ReactiveFormsModule, FormBuilder } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { InspectionService } from '../../core/services/inspection.service';
import { InspectionCreate } from '../../core/models/inspection.models';

@Component({
  selector: 'app-hive-inspect',
  standalone: true,
  imports: [ReactiveFormsModule],
  templateUrl: './hive-inspect.component.html',
  styleUrl: './hive-inspect.component.css',
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class HiveInspectComponent {
  private readonly route = inject(ActivatedRoute);
  private readonly router = inject(Router);
  private readonly inspectionService = inject(InspectionService);
  private readonly fb = inject(FormBuilder);

  protected readonly saving = signal(false);
  protected readonly errorMessage = signal('');
  protected readonly hiveId = Number(this.route.snapshot.paramMap.get('id'));
  protected readonly today = new Date().toISOString().slice(0, 10);

  protected readonly form = this.fb.group({
    date: [this.today],
    queen_seen: [false],
    food_stores: [5],
    varroa_count: [0],
    swarm_cells: ['none'],
    mood: ['normal'],
    strength: ['medium'],
    weather: [''],
    next_steps: [''],
    notes: ['']
  });

  protected save(): void {
    this.saving.set(true);
    const value = this.form.value;
    const payload: InspectionCreate = {
      date: value.date || this.today,
      queen_seen: value.queen_seen ?? false,
      food_stores: value.food_stores ?? undefined,
      varroa_count: value.varroa_count ?? undefined,
      swarm_cells: value.swarm_cells as InspectionCreate['swarm_cells'],
      mood: value.mood as InspectionCreate['mood'],
      strength: value.strength as InspectionCreate['strength'],
      weather: value.weather || undefined,
      next_steps: value.next_steps || undefined,
      notes: value.notes || undefined
    };
    this.inspectionService.createInspection(this.hiveId, payload).subscribe({
      next: () => this.router.navigate(['/beehives', this.hiveId]),
      error: () => {
        this.saving.set(false);
        this.errorMessage.set('Durchsicht konnte nicht gespeichert werden.');
      }
    });
  }
}
