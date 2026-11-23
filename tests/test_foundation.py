from pathlib import Path
base=Path(__file__).resolve().parents[1]
colors=(base/'styles/theme-tokens.css').read_text()
i18n=(base/'scripts/i18n.js').read_text()
assert all(x in colors for x in ['#242424','#F4F0E9','#C98D62','#9D603B','data-theme="light"'])
assert all(x in i18n for x in ['pt-BR','en','ep_locale','data-i18n'])
for f in ['index.html','second.html']:
 s=(base/'demo'/f).read_text()
 assert 'theme-init.js' in s and 'theme.js' in s and 'i18n.js' in s
 assert s.index('theme-init.js') < s.index('theme-tokens.css')
print('OK: colors, translations, two-page test, and theme bootstrap order')
