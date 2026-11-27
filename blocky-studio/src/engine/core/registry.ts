// Named registries: data files refer to sets, clips, moves, looks and programs by id; unknown ids fail loudly.
export class Registry<T> {
  private items = new Map<string, T>();
  constructor(readonly kind: string) {}
  add(id: string, item: T) {
    if (this.items.has(id)) throw new Error(`${this.kind} "${id}" registered twice`);
    this.items.set(id, item);
    return item;
  }
  get(id: string): T {
    const v = this.items.get(id);
    if (!v) throw new Error(`unknown ${this.kind} "${id}". Known: ${[...this.items.keys()].join(", ")}`);
    return v;
  }
  has(id: string) { return this.items.has(id); }
  ids() { return [...this.items.keys()]; }
}
