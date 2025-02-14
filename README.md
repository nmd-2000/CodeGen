This repository implement these 3 following papers:
- [TransCoder-ST: Leveraging Automated Unit Tests for Unsupervised Code Translation](https://arxiv.org/pdf/2110.06773.pdf) (2021)
- [DOBF: A Deobfuscation Pre-Training Objective for Programming Languages](https://arxiv.org/pdf/2102.07492.pdf) (2021)
- [TransCoder: Unsupervised Translation of Programming Languages](https://arxiv.org/pdf/2006.03511.pdf) (2020)


You can find some documentation for each projects in the docs folder:
- (*editted) [TransCoder](docs/transcoder.md).
- [DOBF](docs/dobf.md)
- [TransCoder-ST](docs/TransCoder-ST.md)


## Dependencies
Run [install_env.sh](install_env.sh).
Suggest: run this in new `conda` environment with python >= 3.7

## Data

Data preprocessing pipeline:
- Source code extraction from json (`.json.gz`) and tokenization (`.tok`)
- Train BPE codes and vocab
- Apply BPE (`.bpe`)
- Binarization (`.pth`)
- Symlink folder with appropriate file names for `.pth` (XLM-syml). To be given as `data_path` argument for training.

**For processing monolingual data** Config path and run [get_mono_data.sh](get_mono_data.sh)

**For processing parallel data** Config path and run [get_parallel_data.sh](get_parallel_data.sh)

### BPE
This repository provides wrappers for [fast BPE](codegen_sources/preprocessing/bpe_modes/fast_bpe_mode.py) and [Roberta BPE](codegen_sources/preprocessing/bpe_modes/roberta_bpe_mode.py) at file level.

### Dataset Preprocessing
Raw data should be stored (multiple line) in `.json` and manual zip to `.json.gz`. The source code will try to read those files have name follow this format `{java|python|cpp|safe|unsafe}.000.json.gz`

This repository contains a [pipeline](codegen_sources/preprocessing/preprocess.py) to create programming languages datasets. Now it supports [four datasets modes](codegen_sources/preprocessing/dataset_modes):
- Monolingual (ex: Java source code) (mode=monolingual)
- Monolingual Functions (ex: Java functions) (mode=monolingual_functions)
- Monolingual Obfuscated (ex: Obfuscated Java source code.)
- Monolingual Obfuscated Functions (ex: Obfuscated Java functions)

**For monolingual dataset** (if the dataset is already extract to function level, it can be applied `mode=monolingual` and have the same results as normal file when apply `mode=monolingual_functions`) run the pipeline:

```bash
python -m codegen_sources.preprocessing.preprocess \
<DATA_PATH> \                            # folder containing json.gz
--langs java cpp python  \               # languages to process
--mode monolingual_functions \           # dataset mode
--bpe_mode=fast_bpe \                    # BPE mode. by default it is fast_BPE. can be roberta_bpe
--local=True \                           # Run on your local machine if True. If False run on a cluster (requires submitit setup)
--train_splits=1                         # Number of trainings splits
```
If you give several languages, the BPE codes and vocab will be learned commonly on these languages , so that you will have a common vocabulary to train one model for several languages. If you do not want that, launch the pipeline on every language separatly. [These tests](codegen_sources/preprocessing/tests/pipeline/test_pipeline.py) test the pipeline on different modes. It will give you an overview of the possible options. 

Also, we provide the BPE codes and vocabulary [here](data/bpe/cpp-java-python). These are the codes and vocabulary used for TransCoder and DOBF. They were learned on concatenated C++, Java, and Python data. If you want to use them instead of learning new ones, give the corresponding paths as ```fastbpe_code_path``` and ```fastbpe_vocab_path``` arguments.

**For parallel dataset** There is no easy way to get the parallel dataset like the way we can get monolingual dataset (by query from [BigQuery](docs/googlebigquery.md)). The parallel dataset must be applied the same BPE codes and vocab with the monolingual. Try to use ```fastbpe_code_path``` and ```fastbpe_vocab_path``` arguments when extract the raw data. See the parallel data format at [here](docs/transcoder.md#parallel-validation-and-test-sets)

### For adding new language
In order to preprocess new language, we must add a Processor with at least `tokenize_code`, `detokenize_code` and `extract_functions` methods (detail [here](https://github.com/facebookresearch/CodeGen/issues/42)). Or inherit from TreeSitterProcessor if tree-sitter do support the language. 

**Source code processors**

This repository contains [programming languages processors](codegen_sources/preprocessing/lang_processors/lang_processor.py) for C++, Java and Python. These processors include:
 - tokenization and detokenization
 - obfuscation
 - function extractions 
 
These processors are based on [TreeSitter](https://tree-sitter.github.io/tree-sitter/) parsers. In order to add new languages, if the language is supported as these parsers are available in more than 30 programming languages, one can easily create a new programming language processor, see [java_processor.py](codegen_sources/preprocessing/lang_processors/java_processor.py) for more detail.

Try if this is working correctly then the processor is ready:

```python
from codegen_sources.preprocessing.lang_processors.java_processor import JavaProcessor

java_code = r"""class HelloWorld {
    public static void main(String[] args) {
        System.out.println("Hello, World!"); 
    }
}"""
java_processor = JavaProcessor(root_folder="<YOUR_TREESITER_FOLDER>")
tokenized_java_code = java_processor.tokenize_code(java_code)
print(tokenized_java_code)
```


### For preprocessing Rust safe/unsafe dataset
Instead of create a language processor for Rust, we should duplicate that processor and name it as "SafeProcessor" and "UnsafeProcessor" as they are 2 different languages. See in [here](codegen_sources/preprocessing/lang_processors).

To get the parallel dataset (for evaluate only), run [create_data_parallel](commands/create_data_parallel.py) to get deduplicate or overlap in both set and get the parallel. However, this function only looking for some function have the same name but differ from common name (e.g. `from_bytes_unchecked`, `test_deref_bufmut_forwards`) in the both sets. A manually review are need since this method can be inaccurate.

- To apply pipeline for monolingual data, run [get_mono_data.sh](get_mono_data.sh)
- To apply pipeline for parallel data, run [get_parallel_data.sh](get_parallel_data.sh)

## Model

### Overview
In this repository, we provide [code](codegen_sources/model) to [train](codegen_sources/model/train.py) transformer-based models (code based on [XLM repository](https://github.com/facebookresearch/XLM)). The available training tasks are the following:
- Masked Language Model (MLM)
- Causal Language Model (CLM)
- Supervised Machine translation (MT)
- Classification
- Deobfuscation = DOBF 
- Unsupervised Machine translation = TransCoder (Denoising auto encoding AE + Back Translation BT) 

We [evaluate](codegen_sources/model/src/evaluation/evaluator.py) our models with metrics adapted to each task (e.g. computation accuracy and BLEU score for TransCoder, subtoken score for Deobfuscation).

Also, we provide [wrappers](codegen_sources/wrappers) to fine-tune and evaluate our models on [CodeXGLUE](https://arxiv.org/pdf/2102.04664.pdf) benchmark.


### Download models
We also provide pre-trained models for language modeling, translation and deobfuscation.

You can donwload the following models :
- [MLM](docs/dobf.md#pre-trained-models)
- [TransCoder](docs/transcoder.md#pre-trained-models). Use it to translate some code [here](codegen_sources/model/translate.py).
- [DOBF](docs/dobf.md#pre-trained-models). Use it to deobfuscate some code [here](codegen_sources/model/deobfuscate.py).

### Re train specific models

To have details on how to retrain specific models, please refer to the README specific to each model.
- [TransCoder README](docs/transcoder.md).
- [DOBF README](docs/dobf.md)

*Notes: `_sa` is standed for "stand alone" and `_cl` is standed for "class"*

**Re train MLM:**

```bash
python codegen_sources/model/train.py 

## main parameters
--exp_name mlm \
--dump_path '<YOUR_DUMP_PATH>' \ 

## data / objectives
--data_path '<DATA_PATH>' \ 
--split_data_accross_gpu local \
--mlm_steps 'cpp,java,python' \  # The languages
--add_eof_to_stream true \
--word_mask_keep_rand '0.8,0.1,0.1' \
--word_pred '0.15' \


## model
--encoder_only true \
--n_layers 6  \
--emb_dim 1024  \
--n_heads 8  \
--lgs 'cpp-java-python' \  # The languages
--max_vocab 64000 \
--gelu_activation false \
--roberta_mode false \

#optimization
--amp 2  \
--fp16 true  \
--batch_size 32 \
--bptt 512 \
--epoch_size 100000 \
--max_epoch 100000 \
--split_data_accross_gpu global \
--optimizer 'adam_inverse_sqrt,warmup_updates=10000,lr=0.0001,weight_decay=0.01' \
--save_periodic 0 \
--validation_metrics _valid_mlm_ppl \
--stopping_criterion '_valid_mlm_ppl,10' 
```

To train transcoder from a pretrained model (MLM):
```bash
python codegen_sources/model/train.py   

## main parameters
--exp_name transcoder \
--dump_path '<YOUR_DUMP_PATH>' \ 

## data / objectives
--data_path '<DATA_PATH>' \
--split_data_accross_gpu local \
--bt_steps 'python_sa-java_sa-python_sa,java_sa-python_sa-java_sa,python_sa-cpp_sa-python_sa,java_sa-cpp_sa-java_sa,cpp_sa-python_sa-cpp_sa,cpp_sa-java_sa-cpp_sa' \ # BT Translate step
--ae_steps 'python_sa,java_sa'  \
--lambda_ae '0:1,30000:0.1,100000:0'  \ 
--word_shuffle 3  \
--word_dropout '0.1' \ 
--word_blank '0.3'  \

## model  
--encoder_only False \
--n_layers 0  \
--n_layers_encoder 6  \
--n_layers_decoder 6 \
--emb_dim 1024  \
--n_heads 8  \
--lgs 'cpp_sa-java_sa-python_sa'  \ # The languages
--max_vocab 64000 \
--gelu_activation false \
--roberta_mode false   \ 

## model reloading
--reload_model '<PATH_TO_MLM_MODEL>,<PATH_TO_MLM_MODEL>'  \
--reload_encoder_for_decoder true \
--lgs_mapping 'cpp_sa:cpp,java_sa:java,python_sa:python'  \  # Translate pair

## optimization
--amp 2  \
--fp16 true  \
--tokens_per_batch 3000  \
--group_by_size true \
--max_batch_size 128 \
--epoch_size 50000  \
--max_epoch 10000000  \
--split_data_accross_gpu global \
--optimizer 'adam_inverse_sqrt,warmup_updates=10000,lr=0.0001,weight_decay=0.01' \
--eval_bleu true \
--eval_computation true \
--has_sentence_ids "valid|para,test|para" \
--generate_hypothesis true \
--save_periodic 1 \
--validation_metrics 'valid_python_sa-java_sa_mt_comp_acc'  
```

*Notes:* Validation metrics can set to:
- {java|python|cpp}_{sa|cl}_mt_ppl
- {valid|test}\_{java|python|cpp}_{sa|cl}
- {java|python|cpp}_{sa|cl}_mt_acc
- {java|python|cpp}_{sa|cl}_mt_comp_acc



## References

### TransCoder model (NeurIPS 2020)

[1] B. Roziere*, M.A. Lachaux*, L. Chanussot, G. Lample [Unsupervised Translation of Programming Languages](https://research.fb.com/wp-content/uploads/2020/11/Unsupervised-Translation-of-Programming-Languages.pdf).

```
@article{roziere2020unsupervised,
  title={Unsupervised translation of programming languages},
  author={Roziere, Baptiste and Lachaux, Marie-Anne and Chanussot, Lowik and Lample, Guillaume},
  journal={Advances in Neural Information Processing Systems},
  volume={33},
  year={2020}
}
```

### DOBF

[2] B. Roziere*, M.A. Lachaux*, M. Szafraniec , G. Lample [DOBF: A Deobfuscation Pre-Training Objective for Programming Languages](https://arxiv.org/abs/2102.07492).

```
@article{roziere2021dobf,
  title={{DOBF}: A Deobfuscation Pre-Training Objective for Programming Languages},
  author={Roziere, Baptiste and Lachaux, Marie-Anne and Szafraniec, Marc and Lample, Guillaume},
  journal={arXiv preprint arXiv:2102.07492},
  year={2021}
}
```

### TransCoder-ST
[3] B. Roziere, J.M. Zhang, F. Charton, M. Harman, G. Synnaeve, G. Lample [Leveraging Automated Unit Tests for Unsupervised Code Translation](https://arxiv.org/pdf/2110.06773.pdf).

```
@article{roziere2021leveraging,
  title={Leveraging Automated Unit Tests for Unsupervised Code Translation},
  author={Roziere, Baptiste and Zhang, Jie M and Charton, Francois and Harman, Mark and Synnaeve, Gabriel and Lample, Guillaume},
  journal={arXiv preprint arXiv:2110.06773},
  year={2021}
}
```

*Equal Contribution

## License
The validation and test parallel datasets from GeeksForGeeks, and the evaluation scripts under [data/transcoder_evaluation_gfg](data/transcoder_evaluation_gfg) are released under the Creative Commons Attribution-ShareAlike 2.0 license. See https://creativecommons.org/licenses/by-sa/2.0/ for more information.

The rest of the `CodeGen` repository is under the MIT license. See [LICENSE](LICENSE) for more details.
