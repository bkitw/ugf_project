from django.utils.text import slugify
import random

# Normalizer for slugyfier

CYRILLIC_SYMBOLS = "абвгдеёжзийклмнопрстуфхцчшщъыьэюяєіїґ"
TRANSLATION = ("a", "b", "v", "g", "d", "e", "e", "j", "z", "i", "j", "k",
               "l", "m", "n", "o", "p", "r", "s", "t", "u",
               "f", "h", "ts", "ch", "sh", "sch", "", "y",
               "", "e", "yu", "ja", "je", "i", "ji", "g")

TRANS = {}

for c, l in zip(CYRILLIC_SYMBOLS, TRANSLATION):
    TRANS[ord(c)] = l
    TRANS[ord(c.upper())] = l.upper()


def normalize(name):
    global TRANS
    normalized = ''
    nums = '1234567890'
    for i in name:
        if i.isalpha() is False and i not in nums and not ".":
            i = '_'
            normalized += i
        else:
            normalized += i
    return normalized.translate(TRANS)


# Slugyfier for models
def slugify_instance_name(instance, save=False, new_slug=None):
    if new_slug is not None:
        slug = new_slug
    else:
        slug = slugify(normalize(instance.name))
    Klass = instance.__class__
    qs = Klass.objects.filter(slug=slug).exclude(id=instance.id)
    if qs.exists():
        rand_int = random.randint(100_000, 600_000)
        slug = f'{slug}-{rand_int}'
        return slugify_instance_name(instance, save=save, new_slug=slug)
    instance.slug = slug
    if save:
        instance.save()
    return instance
