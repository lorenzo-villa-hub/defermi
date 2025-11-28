
import os
import numpy as np
import ast

from defermi import DefectsAnalysis

def setup_import(subparsers):
    parser_import = subparsers.add_parser('import',help='Import defect calculations')
    subparsers_import = parser_import.add_subparsers()

    parser_vasp = subparsers_import.add_parser('vasp',help='import from VASP directories')
    setup_import_vasp(parser_vasp)

    return


def setup_import_vasp(parser):
    parser.add_argument('-d','--path-defects',
                        default=os.getcwd(),
                        metavar='',
                        type=str,
                        help='Directory containing defects calculations',
                        dest='path_defects')

    parser.add_argument('-b','--path-bulk',
                        type=str,
                        metavar='',
                        help='Path of the bulk calculation (without defects)',
                        dest='path_bulk')

    parser.add_argument('-C','--common-path',
                        default=None,
                        type=str,
                        metavar='',
                        help='Import only defects calculations that contain this string in the absolute path',
                        dest='common_path')

    parser.add_argument('-co','--correction',
                        default=None,
                        type=str,
                        metavar='',
                        help='Compute finite-size charge correction. Available are "kumagai" or "freysoldt"',
                        dest='get_charge_correction')

    parser.add_argument('-eps','--dielectric-tensor',
                        default=None,
                        type=str,
                        metavar='',
                        help='Dielectric tensor of the pristine material. float,3x1 array ("[1,2,3]") or 3x3 array ("[[1,2,3],[4,5,6],[7,8,9]]")',
                        dest='dielectric_tensor')

    parser.add_argument('-m','--get-multiplicity',
                        default=False,
                        action='store_true',
                        help='Automatically determine the multiplicity of the defect in the simulation cell. Not implemented for interstitials and defect complexes',
                        dest='get_multiplicity')

    parser.add_argument('-bg','--band-gap',
                        default=None,
                        type=float,
                        metavar='',
                        help='Band gap of the pristine material. If not provided it is parsed from the bulk path',
                        dest='band_gap')

    parser.add_argument('-vbm','--valence-band-max',
                        default=None,
                        type=float,
                        metavar='',
                        help='Valence band maximum of the pristine material. If not provided it is parsed from the bulk path',
                        dest='vbm')

    parser.add_argument('-I','--initial-structure',
                        default=False,
                        action='store_true',
                        help='Use the initial structure to determine the position of the defect',
                        dest='initial_structure')

    parser.add_argument('-f','--filename',
                        default='DA.csv',
                        type=str,
                        metavar='',
                        help='Filename to save DefectsAnalysis object',
                        dest='filename')



    parser.set_defaults(func=run_import_vasp)

def run_import_vasp(args):
    if args.dielectric_tensor:
        dielectric_tensor = ast.literal_eval(args.dielectric_tensor)
    else:
        dielectric_tensor = None
    da = DefectsAnalysis.from_vasp_directories(
                    path_defects=args.path_defects,
                    path_bulk=args.path_bulk,
                    common_path=args.common_path,
                    get_charge_correction=args.get_charge_correction,
                    dielectric_tensor=dielectric_tensor,
                    get_multiplicity=args.get_multiplicity,
                    band_gap=args.band_gap,
                    vbm=args.vbm,
                    initial_structure=args.initial_structure
    )
    da.to_file(args.filename)
    return


