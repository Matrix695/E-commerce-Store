from django.core.management.base import BaseCommand
from catalog.models import Product


PRODUCTS = [
    ("Cloud Form Vessel", "cloud-form-vessel", "Objects", "A softly sculptural stoneware vessel, hand-finished with a satin glaze. Made to hold stems, or to be beautiful all by itself.", "5700.00", "photo-1578749556568-bc2c40e68b61", True),
    ("Arc Table Lamp", "arc-table-lamp", "Lighting", "A quiet pool of warm light, shaped by a brushed brass stem and a pleated cotton shade. A small ritual for the end of the day.", "15400.00", "photo-1507473885765-e6ed057f782c", True),
    ("Linen Everyday Throw", "linen-everyday-throw", "Textiles", "European flax linen, washed until it feels like it has always been yours. Naturally breathable, beautifully relaxed.", "10500.00", "photo-1600210492486-724fe5c67fb0", False),
    ("Sunday Serving Bowl", "sunday-serving-bowl", "Table", "An easy, generous bowl for long lunches and weeknight pasta. Turned by hand with subtle variations in every piece.", "4500.00", "photo-1576021182211-9ea8dced3690", True),
    ("Folded Oak Stool", "folded-oak-stool", "Objects", "Solid white oak with rounded edges and a gently curved seat. Equally at home beside the bed or gathered around the table.", "20700.00", "photo-1503602642458-232111445657", False),
    ("Ripple Glass Set", "ripple-glass-set", "Table", "Four tactile glasses with a subtle hand-pressed ripple. Made for sparkling water, natural wine, and everything between.", "3500.00", "photo-1513558161293-cdaf765edfd7", False),
    ("Quiet Hour Candle", "quiet-hour-candle", "Objects", "A clean-burning soy candle with notes of cedar leaf, fig, and a little open window. Poured in a reusable ceramic cup.", "3200.00", "photo-1603006905003-be475563bc59", False),
    ("Gathering Table Runner", "gathering-table-runner", "Textiles", "A softly textured cotton-linen runner in the color of oat milk. Woven in small batches for meals that take their time.", "6300.00", "photo-1604578762246-41134e37f9cc", False),
    ("Pebble Catchall Dish", "pebble-catchall-dish", "Objects", "A small, softly irregular dish for keys, rings, and the everyday things that deserve a place of their own.", "2700.00", "photo-1578749556568-bc2c40e68b61", False),
    ("Cedar Keepsake Box", "cedar-keepsake-box", "Objects", "A compact solid-wood box with a sliding lid, made for the small keepsakes you want close at hand.", "4800.00", "photo-1616486338812-3dadae4b4ace", False),
    ("Washed Cotton Pillowcase Pair", "washed-cotton-pillowcase-pair", "Textiles", "Two breathable cotton pillowcases with a relaxed, lived-in finish and a quiet envelope closure.", "5300.00", "photo-1616486029423-aaa4789e8c9a", False),
    ("Soft Grid Cushion Cover", "soft-grid-cushion-cover", "Textiles", "A textured cotton cover with a subtle woven grid, finished with a hidden zip and made for slow afternoons.", "4000.00", "photo-1600210492486-724fe5c67fb0", False),
    ("Wool Loop Bath Mat", "wool-loop-bath-mat", "Textiles", "A thick, absorbent wool-blend mat with a looped surface and a grounded natural tone.", "7300.00", "photo-1618221195710-dd6b41faaea6", False),
    ("Morrow Wall Sconce", "morrow-wall-sconce", "Lighting", "A compact wall light with a gently angled shade that casts a warm, considered glow beside a bed or reading chair.", "13000.00", "photo-1507473885765-e6ed057f782c", False),
    ("Little Orbit Pendant", "little-orbit-pendant", "Lighting", "A simple pendant with a rounded shade and soft, downward light for a breakfast nook or bedside corner.", "16500.00", "photo-1513506003901-1e6a229e2d15", False),
    ("Studio Desk Light", "studio-desk-light", "Lighting", "A small adjustable task lamp with a weighted base, balanced proportions, and a focused warm beam.", "11900.00", "photo-1507473885765-e6ed057f782c", False),
    ("Paper Shade Floor Lamp", "paper-shade-floor-lamp", "Lighting", "A tall, airy floor lamp with a softly diffused paper shade for gentle light at the end of the day.", "18900.00", "photo-1507473885765-e6ed057f782c", False),
    ("Everyday Stoneware Mug Set", "everyday-stoneware-mug-set", "Table", "A pair of hand-finished mugs with comfortable handles and a glaze that makes each one slightly different.", "3800.00", "photo-1576021182211-9ea8dced3690", False),
    ("Olive Wood Salad Servers", "olive-wood-salad-servers", "Table", "A balanced serving pair carved from responsibly sourced olive wood, with a natural grain that only gets better.", "3000.00", "photo-1490645935967-10de6ba17061", False),
    ("Breakfast Side Plate Pair", "breakfast-side-plate-pair", "Table", "Two small stoneware plates for toast, fruit, and the little things that make a morning feel settled.", "3300.00", "photo-1576021182211-9ea8dced3690", False),
]


class Command(BaseCommand):
    help = "Create the sample products for the Haven storefront."

    def handle(self, *args, **options):
        for name, slug, category, description, price, _photo, featured in PRODUCTS:
            Product.objects.update_or_create(slug=slug, defaults={
                "name": name, "category": category, "description": description, "price": price,
            "image_url": f"/static/catalog/products/{slug}.jpg",
                "image_alt": name, "featured": featured, "available": True,
            })
        self.stdout.write(self.style.SUCCESS(f"Seeded {len(PRODUCTS)} products across four categories."))
