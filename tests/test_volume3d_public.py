"""Fresh-checkout metadata installation must not replace another input version."""
from pathlib import Path
import tempfile,unittest
from experiments.volume3d.setup_inputs import install,INVENTORY


class PublicVolumeInputsTests(unittest.TestCase):
    def test_fresh_install_is_repeatable_and_rejects_changed_inventory(self):
        with tempfile.TemporaryDirectory() as temporary:
            data=Path(temporary)/'data/real/Tangaroa-FAU'
            path=install(data)
            self.assertEqual(path.read_bytes(),INVENTORY.read_bytes())
            self.assertEqual(install(data),path)
            different=b'{"different_archive": true}\n';path.write_bytes(different)
            with self.assertRaisesRegex(ValueError,'Existing inventory differs'):install(data)
            self.assertEqual(path.read_bytes(),different)


if __name__=='__main__':unittest.main()
