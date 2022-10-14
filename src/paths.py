import random
from pathlib import PosixPath as Path


class SamplePath(Path):
    def sample_id(self, return_ext=False):
        return self.name.rsplit(".", 1) if return_ext else self.stem

    def labels_fpath(self):
        return json_path / (self.sample_id() + ".json")

    def background_fpath(self):
        return path_back / self.name


def list_input_images(for_anon=False):
    fnames = [SamplePath(p) for p in Path(path_entrada).iterdir()]
    random.shuffle(fnames)
    for input_fpath in fnames:
        file_id, file_ext = input_fpath.sample_id(return_ext=True)

        bg_labels_file_exists = Path(
            str(input_fpath.labels_fpath()).replace(".json", ".bg.json")
        ).exists()

        valid_fname_extension = file_ext.lower() in ("jpg", "jpeg", "png")

        back_file_exists = input_fpath.background_fpath().exists()
        already_did_anon = back_file_exists and bg_labels_file_exists

        criteria = valid_fname_extension
        if for_anon:
            criteria = criteria and not already_did_anon
        else:
            criteria = criteria and already_did_anon

        if criteria:
            yield SamplePath(input_fpath)


# Arquivo que concentra caminhos utilizados frequentemente.
path_input_base = Path(__file__).parent.parent / "synthesis_input"
path_output_base = Path(__file__).parent.parent / "synthesis_output"

# Path com a imagem.
path_entrada = path_input_base / "input"

# Nome do json de saída do VIA ANNOTATOR com as informações de todas as imagens rotuladas.
json_path = path_input_base / "labels"

# Diretórios que guardam produtos intermediários da síntese
path_back = path_output_base / "back"
path_crop = path_output_base / "crop"
path_mask = path_output_base / "mask"

# Diretório que guardam o produto final da síntese (imagem e anotações)
path_saida = path_output_base / "reboot"

# Diretório que guarda arquivos estáticos, como
path_static = Path(__file__).parent.parent / "files"

# Diretório que guarda o progresso de cada processo (quando executado em parelelo)
path_mpout = Path("/tmp") / "mplock_out"

for p in (path_saida, path_back, path_crop, path_mask):
    p.mkdir(exist_ok=True, parents=True)
