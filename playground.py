import pandas as pd
import configs.general.config as c


programs = pd.read_csv(c.programs_path)
sub = pd.read_csv(c.subjects_path)

diff = set(sub.Name) - set(programs['תת סל'])

sub.Name = sub.Name.replace('קידום שלומות [well-being] של צוותי חינוך', 'קידום שלומות (well being) של צוותי חינוך')
programs['תת סל'] = programs['תת סל'].replace('מנהיגות ומוערבות בלמידה', 'מנהיגות ומעורבות בלמידה')

programs.to_csv(c.programs_path, index=False, encoding='utf-8-sig')
sub.to_csv(c.subjects_path, index=False, encoding='utf-8-sig')
