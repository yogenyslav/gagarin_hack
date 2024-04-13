import { makeAutoObservable } from 'mobx';
export class RootStore {
    selectedAnomalyIds: Set<string> = new Set();

    constructor() {
        makeAutoObservable(this);
    }

    setSelectedAnomalyId(id: string): void {
        if (this.selectedAnomalyIds.has(id)) {
            this.selectedAnomalyIds.delete(id);
        } else {
            this.selectedAnomalyIds.add(id);
        }
    }

    clearSelectedAnomalyIds(): void {
        this.selectedAnomalyIds.clear();
    }

    isAnomalySelected(id: string): boolean {
        return this.selectedAnomalyIds.has(id);
    }

    get selectedAnomalyIdsArray(): string[] {
        return Array.from(this.selectedAnomalyIds).map(String);
    }

    setSelectedAnomalyIds(ids: string[] | string): void {
        if (Array.isArray(ids)) {
            this.selectedAnomalyIds = new Set(ids);
        } else {
            this.selectedAnomalyIds = new Set([ids]);
        }
    }

    convertSecondsToMinutesAndSeconds(seconds: number): string {
        const minutes = Math.floor(seconds / 60);
        const remainingSeconds = seconds % 60;

        return `${minutes}:${remainingSeconds < 10 ? '0' : ''}${remainingSeconds}`;
    }
}
