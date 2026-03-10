class Textbook {
  final String id;
  final String name;
  final String level;

  const Textbook({
    required this.id,
    required this.name,
    required this.level,
  });

  static const nederlandsInGang = Textbook(
    id: 'nig',
    name: 'Nederlands in gang',
    level: 'A0-A2',
  );

  static const nederlandsInActie = Textbook(
    id: 'nia',
    name: 'Nederlands in actie',
    level: 'B1',
  );

  static const nederlandsOpNiveau = Textbook(
    id: 'non',
    name: 'Nederlands op niveau',
    level: 'B2',
  );

  static const all = [nederlandsInGang, nederlandsInActie, nederlandsOpNiveau];
}
